Ans="""
#include<stdio.h>

int main()
{

int n,wt[20],bt[20],tat[20],avwt,avtat=0,i,j;
printf("Enter no of processes(Max 20)\n");

scanf("%d",&n);

printf("Enter Burst Time for\n");

for(i=0;i<n;i++)

{

printf("P[%d]:",i+1);

scanf("%d",&bt[i]);

}

wt[0]=0;

for(i=1;i<n;i++)

{
wt[i]=0;
for(j=0;j<i;j++)
{

wt[i]+=bt[j];

}
}
printf("\nProcess\t\tBurstTime\tWaitingTime\tTurnaroundTime");

for(i=0;i<n;i++)

{

tat[i]=bt[i]+wt[i];
avwt+=wt[i];
avtat+=tat[i];
printf("\nP[%d]\t\t%d\t\t%d\t\t%d",i+1,bt[i],wt[i],tat[i]);

}


avwt/=i;
avtat/=i;
printf("\nAvg Wait Time:%d",avwt);
printf("\nAvg Turn Around Time%d",avtat);
return 0;

}





"""