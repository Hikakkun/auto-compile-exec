#include <stdio.h>

int main() {
    int num1, num2, sum;

    // 標準入力から2つの整数を取得
    printf("2の整数を入力してください: ");
    scanf("%d,%d", &num1, &num2);

    // 2つの整数の合計を計算
    sum = num1 + num2;

    // 合計を出力
    printf("合計は %d です\n", sum);

    return 0;
}
