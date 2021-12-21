#include <iostream>
#include "../demolib2/demolib.h"
using namespace std;

void print_hello() {
    cout << "hello word" << endl;
    print_hello2();
}

void print_demolib() {
    cout << "print demolib" << endl;
}