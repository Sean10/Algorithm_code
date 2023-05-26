class Solution {
public:
    int thirdMax(vector<int>& nums) {
        set<int> set_;
        for (auto i: nums)
        {
            set_.insert(i);
            if(set_.size() > 3)
                set_.erase(set_.begin());
        }
        return set_.size() >= 3 ? *set_.begin() : *set_.rbegin();
    }
};

class Solution {
public:
    int thirdMax(vector<int>& nums) {
        long long max_ = LLONG_MIN, sec_ = LLONG_MIN, third_ = LLONG_MIN;
        unordered_set<int> set_;
        for (auto i: nums)
        {
            if (set_.find(i) != set_.end())
                continue;
            set_.insert(i);
            if (i > max_)
            {
                third_ = sec_;
                sec_ = max_;
                max_ = i;
            }else if (i > sec_)
            {
                third_ = sec_;
                sec_ = i;
            }else if(i > third_)
                third_ = i;
        }
        return third_ == LLONG_MIN ? max_ : third_;
    }
};
