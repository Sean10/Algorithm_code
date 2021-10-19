#include <stdio.h>
#include <pthread.h>
#include <sys/time.h>
/* pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER; */
pthread_mutex_t mutex;

int count;

void * thread_run(void *arg)
{
    int i;
    struct timeval tv;  
    gettimeofday(&tv,NULL);
    printf("before lock time:%d\n", tv.tv_usec);
    pthread_mutex_lock(&mutex);
    gettimeofday(&tv,NULL);
    printf("lock time:%d\n", tv.tv_usec);
    for (i = 0; i < 3; i++) {
        printf("[%#lx]value of count: %d\n", pthread_self(), ++count);
    }
    gettimeofday(&tv,NULL);
    printf("unlock time:%d\n", tv.tv_usec);
    pthread_mutex_unlock(&mutex);

    gettimeofday(&tv,NULL);
    printf("after lock ti e:%d\n", tv.tv_usec);
    return 0;
}

int main(int argc, char *argv[])
{
    pthread_t thread1, thread2;
    pthread_mutex_init(&mutex, 0);
    pthread_create(&thread1, NULL, thread_run, 0);
    pthread_create(&thread2, NULL, thread_run, 0);
    pthread_join(thread1, 0);
    pthread_join(thread2, 0);
    pthread_mutex_destroy(&mutex);
    return 0;
}