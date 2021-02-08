class RandomizedSet {
public:
    /** Initialize your data structure here. */
    RandomizedSet() {
        srand(NULL);
    }

    /** Inserts a value to the set. Returns true if the set did not already contain the specified element. */
    bool insert(int val) {
        if (map_[val] == true)
            return false;
        map_[val] = true;
        val_.push_back(val);
        return true;
    }

    /** Removes a value from the set. Returns true if the set contained the specified element. */
    bool remove(int val) {
        auto it = map_.find(val);
        if(it == map_.end())
            return false;
        map_.erase(it);
        val_.erase(find(val_.begin(), val_.end(), val));
        return true;
    }

    /** Get a random element from the set. */
    int getRandom() {
        return val_[rand()%(val_.size())];
    }

private:
    unordered_map<int, bool> map_;
    vector<int> val_;
};

/**
 * Your RandomizedSet object will be instantiated and called as such:
 * RandomizedSet obj = new RandomizedSet();
 * bool param_1 = obj.insert(val);
 * bool param_2 = obj.remove(val);
 * int param_3 = obj.getRandom();
 */
