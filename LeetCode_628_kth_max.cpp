class Solution {
public:
    int maximumProduct(vector<int>& nums) {
        int ans[2] = {1,1};
        int tmp_max[3];
        int tmp_min[3];

        tmp_max[0] = *max_element(nums.begin(),nums.end());
        nth_element(nums.begin(),nums.begin()+1,nums.end(),[](int x,int y){return x > y;});
        tmp_max[1] = *(nums.begin()+1);
        nth_element(nums.begin(),nums.begin()+2,nums.end(),[](int x,int y){return x > y;});
        tmp_max[2] = *(nums.begin()+2);
        //it_2 = min_element(nums.begin(),nums.end());

        tmp_min[0] = *min_element(nums.begin(),nums.end());
        nth_element(nums.begin(),nums.begin()+1,nums.end());
        tmp_min[1] = *(nums.begin()+1);

        ans[0] = tmp_min[0]*tmp_min[1]*tmp_max[0];
        ans[1] = tmp_max[0]*tmp_max[1]*tmp_max[2];
            //nums.erase(it);

        return ans[0]>ans[1]?ans[0]:ans[1];

    }
};
