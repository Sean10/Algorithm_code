class Solution {
public:
    bool isValidSerialization(string preorder) {
        if (preorder.empty())
            return false;
        stringstream ss(preorder);
        string temp_num;

        int size = 1;
        while(getline(ss, temp_num, ','))
        {

            size -= 1;

            if (size < 0)
                return false;

            if (temp_num != "#"){
                size += 2;
            }
        }
        cout << size;
        return size == 0;
    }
};
