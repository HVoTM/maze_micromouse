# DISJOINT SETS

# Class to implement Disjoint Sets
class DisjointSet:
    # Here we are implementing the sets using array, initializing operation
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n # Optimizing union by rank for now
        # 
    # Inserting a new set
    def make_set(self, x):
        self.parent[x] = x
        self.rank[x] = 0

    # Determine which subset a particular element is in. 
    # This can determine if two elements are in the same subset.
    def find(self, a):
        if self.parent[a] != a:
            self.parent[a] = self.find(self.parent[a])  # Path compression method
            # We recursively call find on its parent and
            # move until we find the representative of this set
        return self.parent[a]
    
    # Join two subsets into a single subset. 
    # Here first we have to check if the two subsets belong to the same set.
    # If not, then we cannot perform union. 
    def union(self, a, b): # Using Union by Rank
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a != root_b: # check if two subsets belong to the same set (same root)
            # if not, proceed
            # check the ranks of the two root of a, b
            # set the parent(or root of the inferior node to the root of the superior one)
            if self.rank[root_a] < self.rank[root_b]:
                self.parent[root_a] = root_b
            elif self.rank[root_a] > self.rank[root_b]:
                self.parent[root_b] = root_a
            # if the two ranks are equal, set the parent of the latter order that we 
            # have set inherently in the code to the former one's
            # REMINDER: maybe call the preceding index as a, and the succeeding one as b
            else:
                self.parent[root_b] = root_a
                self.rank[root_a] += 1

# Driver code to test the data structure
if __name__ == '__main__':
    # Initialize a DisjointSet with 6 elements (0, 1, 2, 3, 4, 5)
    n = 6
    ds = DisjointSet(n)

    # Make individual sets for each element
    for i in range(n):
        ds.make_set(i)

    # Perform Union operations
    ds.union(0, 1)
    ds.union(2, 3)
    ds.union(4, 5)
    ds.union(1, 2)  # Merging two sets
    ds.union(3, 4)  # Merging two sets

    # Find representative elements
    print("Representatives:")
    for i in range(n):
        print(f"Element {i} belongs to the set with representative {ds.find(i)}")

    # Check if elements are in the same set
    print("Are elements in the same set?")
    print(ds.find(0) == ds.find(3))  # Should be True
    print(ds.find(1) == ds.find(5))  # Should be False
