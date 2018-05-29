#!/usr/bin/python2

import p4vasp.matrix as p4m
import numpy as np
import math
import cmath
import sys
import itertools as itt

# convenience functions
def isAlmost(a, b, tiny = 1e-5):
    return abs(a - b) < tiny

def errorExit(str):
    sys.stderr.write("Error: " + str + "\n")
    sys.exit()


class PhononsCalculation(object):
    """Class for phonon calculations.

    This Class accepts input from VASP calculations and manages + uses this
    information to prepare phonon calculations.
    The supplied data structures should be
     * p4vasp.Structure.Structure holding the primitive cell information.
     * p4vasp.Structure.Structure holding the super-cell information.
     * p4vasp.Array.Array holding the force constant matrix entries.
    Optionally, a list containing masses for either the primitive cell or the
    super-cell can be supplied.  Thus, the length of this list must be equal to
    either the number of atoms in the primitive- or the super-cell.
    If a masses list is not supplied the information is gathered from the
    super-cell structure.

    """
    def __init__(self, prim_struct, super_struct, force_const, masses = None):
        self._prim_cell = prim_struct
        self._super_cell = super_struct
        self._force_const = force_const
        self._masses = masses

        self.reset()


    def setPrimitiveCell(prim_struct):
        """Sets a new primitive cell; Internals are recalculated.

        """
        self._prim_cell = prim_struct
        self.reset()

    def setSuperCell(super_struct):
        """Sets a new super-cell; Internals are recalculated.

        """
        self._super_cell = super_struct
        self.reset()

    def setForceConstants(force_const):
        """Sets new force constants; Internals are recalculated.

        """
        self._force_const = force_const
        self.reset()

    def setMasses(masses):
        """Sets new masses; Internals are recalculated.

        """
        self._masses = masses
        self.reset()


    def reset(self):
        """Resets the important fields of the class.

        This is part of the initialization routine and uses the supplied
        structures to construct important containers for later calculations.
        This method can be used to reset the class if desired, for example,
        if the supplied structures have been modified from outside the class.

        """
        # Setup or reset information structures
        self._prim_num = len(self._prim_cell)
        self._super_num = len(self._super_cell)
        self._species_idx = [[] for x in self._prim_cell]
        self._prim_idx = [None for x in self._prim_cell]
        self._shortest_dist = [[[] for a in self._super_cell]
                                   for b in self._prim_cell]

        self._rec_cell = self._prim_cell.getRecipBasis()

        # force constants are used with a negative sign
        self._force_const = [[[[-fc for fc in kart_a]
                                    for kart_a in sup_c]
                                    for sup_c in prim_c]
                                    for prim_c in self._force_const]

        # Generate masses list if necessary
        # !!! This is bugged due to temporary rescale stuff
        if self._masses is None:
            self._masses = [self._super_cell.getRecordForAtom(x)["mass"]
                                for x in range(self._super_num)]

        # !!! This is probably good concerning generality of input but has not
        # been tested.
        self._super_cell.toUnitCell()

        # call further init methods
        self._groupInstances()
        self._calcShortestDistances()

        # Check if the supplied masses list is of the right size
        if len(self._masses) == self._prim_num:
            # extend the masses list to the super-cell
            prim_masses = self._masses
            self._masses = [0 for x in self._super_cell]

            for mu in range(self._prim_num):
                for l in self._species_idx[mu]:
                    self._masses[l] = prim_masses[mu]
        elif len(self._masses) != self._super_num:
            errorExit("List of masses must have the same length as either the "
                      "primitive or the super-cell structure.")


    def _groupInstances(self):
        """INTERNAL; Browses SC and groups all instances of PC atoms together.

        This method browses through all super-cell atoms and groups them
        together based on the primitive cell atom they correspond to.

        """
        # !!! ATM this heavily relies on the assumption that the whole super-
        # cell is always localized within its own giant unit-cell.
        # !!! I have to rethink this statement with the new algo
        self._prim_cell.setCarthesian()
        self._super_cell.setCarthesian()
        for mu, p_atom in enumerate(self._prim_cell):
            # Push PC atom to SC and convert it back to direct PC coordinates
            p_dir_atom = self._prim_cell.cart2dir(p_atom)
            s_dir_atom = self._super_cell.cart2dir(p_atom)
            for i, s_atom in enumerate(self._super_cell):
                # Find all instances of PC atom
                diff = self._prim_cell.cart2dir(s_atom) - p_dir_atom
                if all(isAlmost(x, round(x)) for x in diff):
                    self._species_idx[mu].append(i)
                # Find THE PC atom itself
                # !!! does not work in some cases; disabled for now
                #diff = self._super_cell.cart2dir(s_atom) - s_dir_atom
                #if all(isAlmost(x, round(x)) for x in diff):
                    #self._prim_idx[mu] = i

        # new algo for primitive index -> this produces the right result
        for mu, a in enumerate(self._force_const):
            biggest = 0
            for i, b in enumerate(a):
                big = sum(sum(abs(fc) for fc in c) for c in b)
                if big > biggest:
                    biggest = big
                    self._prim_idx[mu] = i

    def _calcShortestDistances(self):
        """INTERNAL; Gernerates shortest-distance vectors to other SC atoms.

        This method searches for the shortest distance from a primitive cell
        atom to a super-cell atom in the periodical super-cell.
        In the case of ambiguity all equivalent distance vectors are stored in
        a nested list.

        """

        self._prim_cell.setCarthesian()
        self._super_cell.setCarthesian()
        shift_vectors = [self._super_cell.dir2cart([x, y, z])
                            for x in [-1, 0, 1]
                            for y in [-1, 0, 1]
                            for z in [-1, 0, 1]]

        # Generate distance vectors to SC atoms from PC atoms.
        # This also takes care of possible ambiguities.
        for mu, p_atom in enumerate([self._super_cell[x]
                                        for x in self._prim_idx]):
            for i, s_atom in enumerate(self._super_cell):
                if i == self._prim_idx[mu]:
                    self._shortest_dist[mu][i] = [p4m.Vector(0, 0, 0)]
                    continue
                diff_len_old = float('inf')
                del self._shortest_dist[mu][i][:]
                for shift in shift_vectors:
                    diff = p_atom - s_atom - shift
                    diff_len = diff.length()
                    if isAlmost(diff_len, diff_len_old):
                        self._shortest_dist[mu][i].append(diff)
                    elif diff_len < diff_len_old:
                        del self._shortest_dist[mu][i][:]
                        diff_len_old = diff_len
                        self._shortest_dist[mu][i].append(diff)


    def calcPhononFrequencies(self, k_path):
        """Calculates phonon angular frequencies along the given k-point path.

        The supplied path must be an iterable container consisting of
        p4vasp.matrix.Vector objects describing the k-points.
        This method will return the square-roots of the eigenvalues of the
        Dynamical Matrix, namely the angular frequencies of the phonon
        eigenstates.

        """

        self._prim_cell.setCarthesian()
        self._super_cell.setCarthesian()

        # FORCE_CONSTANTS ->  [PC]  [SC]  [Mat Row]  [Mat Column]
        # (just for me)   ->  [mu]  [i]   [alpha]    [beta]
        dyn_mat = [[0
                    for ka in range(3 * self._prim_num)]
                    for mu in range(3 * self._prim_num)]
        first_iteration = True

        # Iterate over all k-points
        for k in k_path:

            # Convert k-point path to carthesian coordinates using the
            # reciprocal basis of the primitive cell; Factor 2 pi !!
            k = self._prim_cell.dir2cart(k, self._rec_cell) * 2 * math.pi

            # Calculate the Dynamical Matrix
            for mu, ka in itt.product(range(self._prim_num), repeat = 2):
                for a, b in itt.product(range(3), repeat = 2):
                    tmp = 0
                    for l in self._species_idx[ka]:
                        phase = sum(cmath.exp(1j * (k * diff))
                                for diff in self._shortest_dist[mu][l])
                        phase /= len(self._shortest_dist[mu][l])

                        # !!! transpose of force const matrix is needed
                        tmp += (self._force_const[mu][l][b][a] * phase)
                    tmp /= math.sqrt(self._masses[self._prim_idx[mu]] *
                            self._masses[l])
                    dyn_mat[mu * 3 + a][ka * 3 + b] = tmp

            # Calculate the eigenvalues and eigenvectors
            dyn_mat = np.array(dyn_mat)
            eig_val, eig_vec = np.linalg.eig(dyn_mat)

            # If eigenvalues are not real print an error and exit
            if not all(isAlmost(z.imag, 0) for z in eig_val):
                errorExit("Dynamical matrix is not hermitian!")
            eig_val = [z.real for z in eig_val]

            # !!! prototype: eigenvalue sorting
            if not first_iteration:
                dimension = len(eig_val)
                delta_val = [0 for x in range(dimension)]
                for j in range(dimension):
                    diff_old = float('inf')
                    idx = 0
                    for l in range(j, dimension):
                        diff_val = eig_val[l] - last_eig_val[j]
                        diff_vec = 1. - abs(np.vdot(eig_vec[l],
                                                    last_eig_vec[j]))
                        # !!! eigenvectors are not used ATM
                        # !!! delta_val seems to give the best results
                        diff = abs(diff_val)
                        diff += abs(diff_val - delta_val[j]) * 100
                        if diff < diff_old:
                            diff_old = diff
                            idx = l
                    # swap
                    eig_val[idx], eig_val[j] = eig_val[j], eig_val[idx]
                    eig_vec[idx], eig_vec[j] = eig_vec[j], eig_vec[idx]

                    delta_val[j] = eig_val[j] - last_eig_val[j]
            else:
                first_iteration = False

            last_eig_val = eig_val
            last_eig_vec = eig_vec

            # Take square roots to return angular frequencies
            omega = [math.sqrt(abs(z)) * np.sign(z) for z in eig_val]
            yield omega

        return
