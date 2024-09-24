#include <stdio.h>
#include "operator.h"
int main(void){
    int a = 10;
    int b = 20;
    printf("%d\n", add(a, b));
    printf("%d\n", sub(a, b));
    return 0;
}