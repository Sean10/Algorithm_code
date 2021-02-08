class Solution {
public:
    string complexNumberMultiply(string a, string b) {
        int ra,rb,ia,ib;
        char buffer;
        stringstream sa(a),sb(b), ans;
        sa >> ra >> buffer >> ia >> buffer;
        sb >> rb >> buffer >> ib >> buffer;
        ans <<  ra*rb-ia*ib << "+" << ra*ib+rb*ia << "i";
        return ans.str();
    }
};
