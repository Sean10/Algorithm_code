class Solution {
public:
    bool canChange(vector<int> &save, int order) {
        if (order == 5)
            return true;
        else if (order == 10) {
            // cout << bool: << (save[0] > 0);
            if (save[0] > 0)
            {
                save[0] --;
                return true;
            }
            return false;
        }
        else {
            if (save[0] > 0 && save[1] > 0)
            {
                save[0] -- ;
                save[1] --;
                return true;
            }
            else if (save[0] > 2)
            {
                save[0] -= 3;
                return true;
            }
            return false;
        }
        return false;
    }
    
    bool lemonadeChange(vector<int>& bills) {
        vector<int> save(4, 0);    
        
        // save = new vector<int>(2, 0);
        for (auto i: bills) {
            if (canChange(save, i)) {
                // cout << bills << i << endl;
                save[i/5-1]++;
                continue;
            }
            // cout << dont return? ;
            return false;
        }
        return true;
    }
    
// private:
};
