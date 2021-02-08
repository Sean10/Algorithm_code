class Solution {
public:
    int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
        int total(0), start(0), tank(0);

        for (int i = 0;i < gas.size(); i++)
        {
            if ((tank = tank+gas[i]-cost[i]) < 0)
            {
                total += tank;
                start = i+1;
                tank = 0;
            }
        }

        return total+tank < 0 ? -1 : start;
    }
};
