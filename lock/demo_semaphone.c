

#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <sys/time.h>
#include <string.h>
#include <errno.h>
#define MAXNUM 2
sem_t semDownload;
pthread_t a_thread, b_thread, c_thread;
void check()
{
	int ret = 0;
    int g_phreadNum = 0;

	ret = sem_getvalue(&semDownload, &g_phreadNum);
	if (0 != ret){
		perror("sem getvalue error: \n");
	}
	printf("current value: %d\n", g_phreadNum);
	//线程数超过2个则不下载
	if (g_phreadNum <= 0) {
		printf("!!! You've reached a limit on the number of threads !!!\n");
	}
}

void InputInfo(void)
{
	printf("****************************************\n");
	printf("*** which task you want to download? ***\n");
	printf("*** you can enter [1-3],[0] is done  ***\n");
	printf("****************************************\n");
}
void *func1(void *arg)
{
	check();
	//等待信号量的值>0
	sem_wait(&semDownload);
	printf("==============  Downloading Task 1  ============== \n");
	sleep(5);
	printf("==============    Finished Task 1   ============== \n");
	//等待线程结束 
	// pthread_join(a_thread, NULL);
}

void *func2(void *arg)
{
	check();

	sem_wait(&semDownload);
	printf("==============  Downloading Task 2  ============== \n");
	sleep(3);
	printf("==============    Finished Task 2   ============== \n");
	// pthread_join(b_thread, NULL);
}

void *func3(void *arg)
{
	check();
	sem_wait(&semDownload);
	printf("==============  Downloading Task 3  ============== \n");
	sleep(1);
	printf("==============    Finished Task 3   ============== \n");
	// pthread_join(c_thread, NULL);
}



int main()
{
	int taskNum;
	InputInfo();
	while (scanf("%d", &taskNum) != EOF) {
		//输入0,判断生产2个允许下载
		if (taskNum == 0) {
			for (int j = 0; j < MAXNUM; j++)
				sem_post(&semDownload);

			continue;
		}

                //初始化信号量
		sem_init(&semDownload, 0, 0);
		printf("your choose Downloading Task [%d]\n", taskNum);


		//用户选择下载Task
		switch (taskNum)
		{
		case 1:
			//创建线程1
			pthread_create(&a_thread, NULL, func1, NULL);
			//信号量+1，进而触发fun1的任务
			break;
		case 2:
			pthread_create(&b_thread, NULL, func2, NULL);
			// sem_post(&semDownload);
			break;
		case 3:
			pthread_create(&c_thread, NULL, func3, NULL);
			// sem_post(&semDownload);
			break;
		default:
			printf("!!! eroor task [%d]  !!!\n", taskNum);
			break;
		}
		InputInfo();
	}

	//销毁信号量
	sem_destroy(&semDownload);
	return 0;
}
