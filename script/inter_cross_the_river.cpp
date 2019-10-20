#include <iostream>
#include <algorithm>
using namespace std;

const int MAXN = 1000;
int cmp(const void *x,const void *y)
{
    return *(int *)x-*(int *)y;
}
int main()
{
    cout<<"热门智力题 - 过桥问题"<<endl;
    cout<<"  --by MoreWindows( http://blog.csdn.net/MoreWindows )--\n"<<endl;

    int n, i, sum, a[MAXN];
    cout<<"请输入人数：";
    cin>>n;
    cout<<"请输入每个人过桥时间，以空格分开"<<endl;
    for (i = 0; i < n; i++)
        cin>>a[i];
    qsort(a, n, sizeof(a[0]), cmp);
    sum = 0;
    for (i = n - 1; i > 2; i = i - 2)
    {
        //最小者将最大2个送走或最小2个将最大2个送走
        if (a[0] + a[1] + a[1] + a[i] < a[0] + a[0] + a[i - 1] + a[i])
            sum = sum + a[0] + a[1] + a[1] + a[i];
        else
            sum = sum + a[0] + a[0] + a[i - 1] + a[i];
    }
    if (i == 2)
        sum = sum + a[0] + a[1] + a[2];
    else if (i == 1)
        sum = sum + a[1];
    else
        sum = a[0];
    cout<<"最短过桥时间为："<<sum<<endl;
    return 0;
}
