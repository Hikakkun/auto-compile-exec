#include <stdio.h>
#include "operator.h"
int main(void){
    int a[2];
    scanf("%d", &a[0]);
    scanf("%d", &a[1]);
    //無限ループ
    while(1){}
    printf("%d\n", add(a[0], a[1]));
    printf("%d\n", sub(a[0], a[1]));
    printf("%d\n", mul(a[0], a[1]));
    printf("%d\n", dev(a[0], a[1]));
    int tmp = a[0];
    a[0] = a[1];
    a[1] = tmp;
    printf("%d\n", sub(a[0], a[1]));
    return 0;
}