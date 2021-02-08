// A full tree
//这这棵树的偶数位和其父节点值不变怎么看出来的
class Solution {
public:
    int kthGrammar(int N, int K) {
        K -= 1;
        int cnt = 0;
        while(K)
        {
            cnt += K&1;
            K >>= 1;
        }

        return cnt%2;
    }
};

class Solution {
public:
    int kthGrammar(int N, int K) {
        long s = pow(2, N-1), flips = 0;
        while(s > 2)
        {
            if (K > s/2)
            {
                K -= s/2;
                flips ++;
            }
            s /= 2;
        }

        return flips&1 ? K%2 : K-1;
    }
};
