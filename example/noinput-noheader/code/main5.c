#include <stdio.h>

int main(void){
    int a[2] = {0, 1};
    printf("%d\n", a[0]);
    printf("%d\n", a[1]);
    //配列外参照
    a[3] = 10;
    return 0;
}