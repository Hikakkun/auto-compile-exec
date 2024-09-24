#include <stdio.h>

int main(void){
    int a[2] = {0, 1};
    printf("%d\n", a[0]);
    printf("%d\n", a[1]);
    //アーキテクチャによってはSegmentation faultが発生しない
    printf("%d\n", a[1000000]);
    return 0;
}