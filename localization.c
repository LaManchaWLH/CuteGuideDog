#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define pi 3.14159265358979323846
#define cntDist 0.1
int main()
{
    int lastLeftCnt, lastRightCnt, curLeftCnt, r, curRightCnt;
    float dLeft, dRight, dth, curTh, leftX, leftY, rightX, rightY;
    lastRightCnt = lastLeftCnt = curLeftCnt = curRightCnt = 0;
    leftY = leftX = rightY = rightX = 0;
    curTh = pi/2;
    r = 20;
    while (1>0)
    {  
        //input curLeftCnt, curRightCnt
        scanf("%d %d",&curLeftCnt, &curRightCnt);
        if (curLeftCnt == -1) break;
        dLeft = (curLeftCnt - lastLeftCnt) * cntDist;  
        dRight = (curRightCnt - lastRightCnt) * cntDist;
        dth = (dLeft - dRight) / r;
        leftX += dLeft * cos(curTh);
        leftY += dLeft * sin(curTh);
        rightX += dRight * cos(curTh);
        rightY += dRight * sin(curTh);
        curTh -= dth;
        lastRightCnt = curRightCnt;
        lastLeftCnt = curLeftCnt;

        printf("dLeft = %.2f, dRight = %.2f, dth = %.2f\n", dLeft, dRight, dth);
        printf("(%.2f, %.2f), (%.2f, %.2f),head towards %.2f\n", leftX, leftY, rightX,  rightY, curTh/pi*180);

    }   
        

}