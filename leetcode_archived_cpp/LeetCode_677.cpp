class MapSum {
public:
    /** Initialize your data structure here. */
    MapSum() {

    }

    void insert(string key, int val) {
        map_[key] = val;
    }

    int sum(string prefix) {
        int n = prefix.size(), sum = 0;
        for(auto i = map_.lower_bound(prefix); i != map_.end() && i->first.substr(0, n) == prefix; i++)
            sum += i->second;
        return sum;
    }
    private:
    map<string, int> map_;
};

/**
 * Your MapSum object will be instantiated and called as such:
 * MapSum obj = new MapSum();
 * obj.insert(key,val);
 * int param_2 = obj.sum(prefix);
 */
