#include <iostream>
#include "../demolib2/demolib2.h"
#include "demolib.h"
using namespace std;
// class A;

void A::print_demolib() {
    cout << "print demolib" << endl;
}


void print_hello() {
    cout << "hello word" << endl;
    class A a;
    print_hello2(&a);
}

