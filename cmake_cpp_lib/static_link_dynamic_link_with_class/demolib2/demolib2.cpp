#include <iostream>
#include "../demolib/demolib.h"

using namespace std;

void print_hello2(class A* a) {
    cout << "hello word demolib2" << endl;
    a->print_demolib();
}