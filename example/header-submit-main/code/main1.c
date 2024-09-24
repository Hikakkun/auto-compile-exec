#include <stdio.h>
#include "operator.h"
int main(void){
    int a, b;
    scanf("%d", &a);
    scanf("%d", &b);
    printf("%d\n", add(a, b));
    printf("%d\n", sub(a, b));
    return 0;
}