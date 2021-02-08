class MyCalendarTwo {
public:
MyCalendarTwo() {

}

bool book(int start, int end) {
	int max_ = INT_MIN, min_ = INT_MAX;
	vector<pair<int, int>> double_store;

	for (auto i: store)
	{
		max_ = max(start, i.first);
		min_ = min(end, i.second);
		if (max_ < min_)
		{
			// cout << start << " " << end << " "<< i.first << " " << i.second << endl;

			for (auto j: double_store)
			{
				if (max(max_, j.first) < min(min_, j.second))
				{
					// cout << "double:" << " " << max_ << " " << min_ << " "<< j.first << " " << j.second << endl;
					return false;
				}
			}
			double_store.push_back({max_, min_});



		}
	}
	store.push_back({start, end});

	return true;
}

private:
vector<pair<int, int>> store;
};

/**
* Your MyCalendarTwo object will be instantiated and called as such:
* MyCalendarTwo obj = new MyCalendarTwo();
* bool param_1 = obj.book(start,end);
*/
