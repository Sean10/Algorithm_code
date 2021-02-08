class MyCalendar {
public:
    MyCalendar() {

    }

    bool book(int start, int end) {
        for (auto i: store)
        {
            if (max(start, i.first) < min(end, i.second))
                return false;
        }
        store.push_back(make_pair(start, end));
        return true;
    }

private:
    vector<pair<int, int>> store;
};

/**
 * Your MyCalendar object will be instantiated and called as such:
 * MyCalendar obj = new MyCalendar();
 * bool param_1 = obj.book(start,end);
 */
