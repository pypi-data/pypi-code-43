Ans="""
#include<stdio.h>

void main()
{
FILE *fptr;
char name[20];
int age;
float sal;
fptr=fopen("emp.txt","w");
if(fptr==NULL)
{
printf("file does not exist\n");
return;
}
printf("Enter the name\n");
scanf("%s",name);
fprintf(fptr,"name=%s\n",name);
printf("enter the age\n");
scanf("%d",&age);
fprintf(fptr,"age=%d\n",age);
printf("enter the salary\n");
scanf("%f",&sal);
fprintf(fptr,"sal=%f\n",sal);
fclose(fptr);
}



"""