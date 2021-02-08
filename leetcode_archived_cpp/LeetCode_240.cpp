class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        if(matrix.empty() || matrix[0].empty())
            return false;

        int i = 0, j = matrix[0].size()-1;
        while(i <= matrix.size()-1 && j >= 0)
        {
            if(matrix[i][j] == target)
                return true;
            else if(matrix[i][j] < target)
                i++;
            else
                j--;

        }
        return false;
    }
};



class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        if(matrix.empty() || matrix[0].empty())
            return false;
        return searchMatrixTarget(matrix, target, 0, matrix.size()-1);
    }

    bool searchMatrixTarget(vector<vector<int>>& matrix, int target, int left, int right)
    {
        if(left > right)
            return false;

        int mid = left + (right-left)/2;
        if(target >= matrix[mid].front() && target <= matrix[mid].back())
            if(searchVector(matrix[mid], target))
                return true;

        cout << "1" ;
        if(searchMatrixTarget(matrix, target, mid+1, right)) return true;
        if(searchMatrixTarget(matrix, target, left, mid-1)) return true;
        return false;
    }

    bool searchVector(vector<int> matrix, int target)
    {
        int left = 0, right = matrix.size()-1;
        while(left <= right)
        {
            cout << '2';
            int mid = left + (right-left)/2;
            if(target == matrix[mid])
                return true;
            else if(target > matrix[mid])
                left = mid+1;
            else
                right = mid-1;
        }
        return false;
    }
};


// 有逻辑漏洞
class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        int ml = 0, mr = matrix.size()-1, nl = 0, nr = matrix[0].size()-1;
        int left = matrix[0][0], right = matrix[mr][nr];
        while(left < right)
        {
            cout << left << '\t' << right << endl;
            int mid = left+(right-left)/2;
            int i = mr;
            while(i >= ml && matrix[i][nl] > mid)
                i--;
            int j = nr;
            while(j >= nl && matrix[ml][j] > mid)
                j--;
            if(mid >= target)
            {
                mr = i;
                nr = j;
                right = matrix[mr][nr];
            }else
            {
                ml = i;
                nl = j;
                left = matrix[ml][nl];
            }


        }
        if(left == target)
            return true;
        return false;
    }
};
