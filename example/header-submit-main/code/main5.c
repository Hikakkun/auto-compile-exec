#include <stdio.h>
#include "operator.h"
int main(void){
    int a[2];
    scanf("%d", &a[0]);
    scanf("%d", &a[1]);
    printf("%d\n", add(a[0], a[1]));
    printf("%d\n", sub(a[0], a[1]));
    printf("%d\n", mul(a[0], a[1]));
    printf("%d\n", dev(a[0], a[1]));
    int tmp = a[0];
    a[0] = a[1];
    a[1] = tmp;
    // 配列外参照
    printf("%d\n", sub(a[0], a[1000000]));
    return 0;
}