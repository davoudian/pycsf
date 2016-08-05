from collections import OrderedDict
import json
import numpy as np
from acq4.pyqtgraph.Qt import QtGui, QtCore


IONS = OrderedDict([('Na', 1), ('K', 1), ('Cl', -1), ('Ca', 2), ('Mg', 2), ('SO4', -2), ('PO4', -3), ('Cs', 1)])


DEFAULT_REAGENTS = [
    ('Monovalent Ions', 'sodium chloride', 'NaCl', 58.44, 1.84, 1, 0, 1),
    ('Monovalent Ions', 'potassium chloride', 'KCl', 74.56, 1.84, 0, 1, 1),
    ('Monovalent Ions', 'potassium phosphate monobasic', 'KH2PO4', 136.09, 2.0, 0, 1, 0, 0, 0, 0, 1),
    ('Monovalent Ions', 'potassium gluconate', '', 234.2, 2.0, 0, 1),
    ('Monovalent Ions', 'cesium methanesulfonate', 'CsMeSO3', 228.0, 2.0, 0, 0, 0, 0, 0, 0, 0, 1),
    ('Monovalent Ions', 'cesium chloride', 'CsCl', 228.0, 2.0, 0, 0, 1, 0, 0, 0, 0, 1),
    ('Sodium Substitutes', 'n-methyl-d-glucamine', 'NMDG', 195.22, 1.0),
    ('Sodium Substitutes', 'tris HCl', '', 157.6, 2.0, 0, 1),
    ('Sodium Substitutes', 'tris base', '', 121.1, 1.0),
    ('Sodium Substitutes', 'choline chloride', '', 139.63, 2.0, 0, 0, 1),
    ('Buffers', 'sodium bicarbonate', 'NaHCO3', 84.01, 2.0, 1),
    ('Buffers', 'sodium phosphate monobasic', 'NaH2PO4 (H2O)', 137.99, 2.0, 1, 0, 0, 0, 0, 0, 1),
    ('Buffers', 'sodium phosphate dibasic', 'Na2HPO4 (7H2O)', 268.1, 3.0, 2, 0, 0, 0, 0, 0, 1),
    ('Buffers', 'HEPES', '', 238.3, 1.0),
    ('Sugars', 'glucose', '', 180.16, 1.0),
    ('Sugars', 'sucrose', '', 342.3, 1.0),
    ('Sugars', 'myo-inositol', '', 180.16, 1.0),
    ('Metabolites', 'sodium pyruvate', '', 110.04, 2.0),
    ('Antioxidants', 'ascorbic acid', '', 176.12, 1.0),
    ('Antioxidants', 'sodium l-ascorbate', '', 198.11, 2.0, 1),
    ('Antioxidants', 'n-acetyl-l-cysteine', '', 163.2, 1.0),
    ('Divalent Ions', 'magnesium sulfate', 'MgSO4 (7H2O)', 246.48, 2.0, 0, 0, 0, 0, 1, 1),
    ('Divalent Ions', 'calcium chloride', 'CaCl2 (2H2O)', 147.02, 3.0, 0, 0, 2, 1),
    ('Divalent Ions', 'calcium chloride (anhydrous)', 'CaCl2', 110.98, 3.0, 0, 0, 2, 1),
    ('Divalent Ions', 'magnesium chloride', 'MgCl2 (6H2O)', 203.31, 3.0, 0, 0, 2, 0, 1),
    ('Energy sources', 'phosphocreatine bg', '', 453.4, 1.0),
    ('Energy sources', 'phosphocreatine disodium hydrate', '', 255.08, 3.0, 2),
    ('Energy sources', 'sodium phosphocreatine', '', 233.09, 2.0, 1),
    ('Energy sources', 'magnesium ATP', '', 507.2, 2.0, 0, 0, 0, 0, 1),
    ('Energy sources', 'disodium ATP', '', 551.14, 3.0, 2),
    ('Energy sources', 'GTP tris', '', 523.2, 2.0),
    ('Energy sources', 'GTP sodium hydrate', '', 523.18, 2.0, 1),
    ('Energy sources', 'disodium GTP', '', 0.0, 3.0, 2),
    ('Toxins', 'picrotoxin', '', 0.0, 1.0),
    ('Toxins', 'QX314 Cl', '', 298.85, 2.0, 0, 0, 1),
    ('Markers', 'biocytin', '', 372.48, 1.0),
    ('Markers', 'alexaflour 488', '', 0.0, 1.0),
    ('Misc', 'EGTA', '', 380.35, 1.0),
    ('Misc', 'taurine', '', 0.0, 1.0),
    ('Misc', 'thiourea', '', 0.0, 1.0),
    ('Misc', 'kyneurenic acid', '', 0.0, 1.0),
    ('Acids/bases', 'hydrochloric acid', 'HCl', 36.46, 0.7),
    ('Acids/bases', 'potassium hydroxide', 'KOH', 0.0, 1.0, 0, 1),
    ('Acids/bases', 'cesium hydroxide', 'CsOH', 0.0, 1.0, 0, 1),
]



class Reagents(QtCore.QObject):
    """A table of reagents and their properties.
    """
    sigReagentListChanged = QtCore.Signal(object)  # self
    sigReagentDataChanged = QtCore.Signal(object)  # self
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        self._dtype = [
            ('group', object),
            ('name', object),
            ('formula', object),
            ('molweight', float),
            ('osmolarity', float),
        ] + [(ion, float) for ion in IONS] + [('notes', object)]
        self._null = (None, None, None, 0, 0, 0) + (0,)*len(IONS) + (None,)
        self.data = np.empty(len(DEFAULT_REAGENTS), dtype=self._dtype)
        for i, reagent in enumerate(DEFAULT_REAGENTS):
            self.data[i] = reagent + (0,)*(len(self._dtype)-len(reagent))

    def add(self, **kwds):
        assert kwds['name'] not in self.data['name'], 'Reagent with this name already exists.'
        self.data = np.resize(self.data, len(self.data)+1)
        self.data[-1] = self._null
        #if 'ions' in kwds:
            #for k,v in kwds.pop('ions').items():
                #self.data[-1]['ions'][k] = v
        for k,v in kwds.items():
            self.data[-1][k] = v
        
        self.sigReagentListChanged.emit(self)

    def remove(self, name):
        try:
            i = np.argwhere(self.data['name'] == name)[0, 0]
        except IndexError:
            raise KeyError('No reagent named "%s"' % name)
        mask = np.ones(len(self.data), dtype=bool)
        mask[i] = False
        self.data = self.data[mask]

        self.sigReagentListChanged.emit(self)

    def save(self):
        return _saveArray(self.data)
    
    def restore(self, data):
        self.data = _loadArray(data, self._dtype)

    def groups(self):
        return np.unique(self.data['group'])

    def __getitem__(self, names):
        if isinstance(names, basestring):
            names = [names]
            returnone = True
        else:
            returnone = False
        
        inds = []
        for n in names:
            r = np.argwhere(self.data['name'] == n)[:,0]
            if r.shape[0] == 0:
                continue
            inds.append(int(r[0]))

        if returnone:
            return self.data[inds[0]]
        else:
            return self.data[inds]


class Solutions(QtCore.QObject):
    """Collection of grouped Solutions.
    """
    solutionListChanged = QtCore.Signal(object)  # self
    solutionDataChanged = QtCore.Signal(object, object)  # self, solution
    
    def __init__(self, db):
        self.db = db
        QtCore.QObject.__init__(self)
        self._data = []
        self.groups = []

    def add(self, soln=None, name=None, group=None):
        if soln is None:
            soln = Solution(name=name, group=group)
        soln.db = self.db
        for s in self._data:
            if s.name == soln.name:
                raise NameError("Solution with this name already exists.")
        self._data.append(soln)
        self.solutionListChanged.emit(self)
    
    def __getitem__(self, name):
        for sol in self._data:
            if sol.name == name:
                return sol
        raise KeyError(name)

    def __iter__(self):
        for soln in self._data:
            yield soln
    
    def restore(self, data):
        self._data = []
        for d in data:
            sol = Solution(db=self.db)
            sol.restore(d)
            self._data.append(sol)
        self.solutionListChanged.emit(self)
    
    def save(self):
        state = []
        for sol in self._data:
            state.append(sol.save())
        return state

    def recalculate(self, solutions, temperature):
        """Return estimated ion concentrations, osmolarity, and reversal potentials."""
        results = {}
        for soln in solutions:
            ions, osm = soln.recalculate()

            if soln.compareAgainst is None:
                revs = {ion: None for ion in IONS}
            else:
                against = self[soln.compareAgainst].recalculate()[0]
                if soln.type == 'external':
                    external = ions
                    internal = against
                else:
                    external = against
                    internal = ions
                R = 8.31446
                T = temperature + 273.15
                F = 96485.333
                revs = {}
                for ion, z in IONS.items():
                    if internal[ion] == 0 and external[ion] == 0:
                        revs[ion] = None
                    else:
                        revs[ion] = 1000 * ((R * T) / (z * F)) * np.log((external[ion]+1e-6) / (internal[ion]+1e-6))
        
            results[soln.name] = [ions, osm, revs]
            
        return results


class Solution(QtCore.QObject):
    """Defines the list of reagents and their concentrations in a solution.
    """
    sigSolutionChanged = QtCore.Signal(object)  # self
    
    def __init__(self, name=None, group=None, against=None, db=None):
        QtCore.QObject.__init__(self)
        self.db = db
        self.name = name
        self.group = group
        self.type = 'internal' if group is not None and 'internal' in group.lower() else 'external'
        self.compareAgainst = against
        self.reagents = {}
        
        # empirically determined values:
        self.ionConcentrations = {}
        self.osmolarity = None
        
    def __setitem__(self, name, concentration):
        """Set the concentration of a particular reagent.
        """
        if concentration in (0,  None):
            self.reagents.pop(name, None)
        else:
            self.reagents[name] = concentration
        self.sigSolutionChanged.emit(self)
        
    def ___getitem__(self, name):
        """Return the concentration of a reagent.
        """
        return self.reagents[name]
    
    def save(self):
        return {'name': self.name, 'group': self.group, 'reagents': self.reagents,
                'type': self.type, 'compareAgainst': self.compareAgainst}
    
    def restore(self, state):
        self.reagents.clear()
        self.reagents.update(state['reagents'])
        self.name = state['name']
        self.group = state['group']
        self.type = state['type']
        self.compareAgainst = state['compareAgainst']

    def recalculate(self):
        """Calculate ion concentrations and osmolarity.
        """
        reagents = self.db.reagents
        knownReagents = [r for r in self.reagents.keys() if r in reagents.data['name']]
        reagents = reagents[knownReagents]
        concs = np.array([self.reagents[n] for n in reagents['name']])
        ions = {}
        for ion in IONS:
            ions[ion] = np.sum(reagents[ion] * concs)
        
        osm = np.sum(concs * reagents['osmolarity'])
        return ions, osm


def _saveArray(data):
    return [_recToDict(rec) for rec in data]
    
def _recToDict(rec):
    od = OrderedDict()
    for field in rec.dtype.names:
        if rec.dtype.fields[field][0].names is None:
            od[field] = rec[field]
        else:
            od[field] = _recToDict(rec[field])
    return od
    

def _loadArray(data, dtype):
    arr = np.empty(len(data), dtype=dtype)
    for i,rec in enumerate(data):
        _loadRec(arr[i], rec)
    return arr
        
def _loadRec(arr, rec):
    for field in arr.dtype.names:
        if arr.dtype.fields[field][0].names is None:
            arr[field] = rec[field]
        else:
            _loadRec(arr[field], rec[field])
        

class Recipe(object):
    """Defines a list of volumes for which reagent masses should be calculated
    for a particular solution.
    """
    
    def __init__(self, solution=None, volumes=None, notes=None, db=None):
        self.db = db
        self.solution = solution
        self.volumes = [] if volumes is None else volumes
        self.notes = notes

    def save(self):
        return {'solution': self.solution.name, 'volumes': self.volumes, 'notes': self.notes}

    def restore(self, state):
        self.notes = state['notes']
        self.volumes = state['volumes']
        self.solution = self.db.solutions[state['solution']]

    def copy(self):
        r = Recipe()
        r.volumes = self.volumes[:]
        r.notes = self.notes
        r.solution = self.solution
        return r


class RecipeSet(QtCore.QObject):
    """Multiple Recipes meant to be displayed together.
    """
    sigRecipeListChanged = QtCore.Signal(object)  # self
    
    def __init__(self, name=None, recipes=None, order=None, stocks=None, db=None):
        QtCore.QObject.__init__(self)
        self.db = db
        self.name = name
        self._recipes = [] if recipes is None else recipes
        self.reagentOrder = [] if order is None else order
        # concentrations of stock solutions per reagent
        self.stocks = {} if stocks is None else stocks  
        self.showMW = False
        self.showConcentration = False

    def add(self, r):
        self._recipes.append(r)
        self.sigRecipeListChanged.emit(self)
        
    def remove(self, r):
        self._recipes.remove(r)
        self.sigRecipeListChanged.emit(self)

    def __iter__(self):
        for r in self._recipes:
            yield r
            
    def __len__(self):
        return len(self._recipes)
        
    def __getitem__(self, i):
        return self._recipes[i]
        
    def save(self):
        recipes = [r.save() for r in self._recipes]
        return {'name': self.name, 'order': self.reagentOrder[:], 'stocks': self.stocks.copy(),
                'showMW': self.showMW, 'showConcentration': self.showConcentration,
                'recipes': recipes} 

    def restore(self, state):
        self.__dict__.update(state)
        self._recipes = []
        for rstate in state['recipes']:
            r = Recipe(db=self.db)
            r.restore(rstate)
            self._recipes.append(r)
        self.sigRecipeListChanged.emit(self)

    def copy(self, name):
        rs = RecipeSet(db=self.db)
        rs.restore(self.save())
        rs.name = name
        rs.recipes = [r.copy() for r in self._recipes]
        return rs


class RecipeBook(QtCore.QObject):
    """A simple collection of RecipeSets.
    """
    sigRecipeSetListChanged = QtCore.Signal(object)  # self
    
    def __init__(self, db=None):
        QtCore.QObject.__init__(self)
        self.db = db
        self._recipeSets = []

    def save(self):
        return [r.save() for r in self._recipeSets]

    def add(self, rs):
        self._recipeSets.append(rs)
        rs.db = self.db
        self.sigRecipeSetListChanged.emit(self)

    def remove(self, rs):
        self._recipeSets.remove(rs)
        self.sigRecipeSetListChanged.emit(self)

    def restore(self, state):
        self._recipeSets = []
        for s in state:
            rs = RecipeSet(db=self.db)
            rs.restore(s)
            self._recipeSets.append(rs)
        self.sigRecipeSetListChanged.emit(self)

    def __getitem__(self, i):
        return self._recipeSets[i]

    def __len__(self):
        return len(self._recipeSets)

    def __iter__(self):
        for rs in self._recipeSets:
            yield rs


class SolutionDatabase(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.reagents = Reagents()
        self.solutions = Solutions(db=self)
        self.recipes = RecipeBook(db=self)
        
    def save(self):
        return {
            'reagents': self.reagents.save(),
            'solutions': self.solutions.save(),
            'recipes': self.recipes.save(),
        }
        
    def restore(self, state):
        self.reagents.restore(state['reagents'])
        self.solutions.restore(state['solutions'])
        self.recipes.restore(state['recipes'])
