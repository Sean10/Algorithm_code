#include<stdio.h>
#include<stdlib.h>

#define ok 1
#define error 0

typedef struct node {
    int i, j;
    int e;
    struct node *right, *down;
} node, *linklist;

typedef struct {
    int mu, nu, tu;
    linklist *row_head, *col_head;
} cross_list;

int initCrossList(cross_list *M) {
    M->row_head = M->col_head = NULL;
    M->nu = M->mu = M->tu = 0;
    return ok;
}




int createCrossList(cross_list *M) {
    linklist bulid, p, judge;//pointer
    int m, n, t, i, j, e, k, judge_number;
    printf("输入稀疏矩阵的行，列以及非零元素个数\n");
    scanf("%d%d%d", &m, &n, &t);
    M->mu = m;
    M->nu = n;
    M->tu = t;
//  行，和列进行初始化
    M->row_head = (linklist *) malloc((m + 1) * sizeof(linklist));
    for (k = 1; k <= m; k++) {
        M->row_head[k] = NULL;
    }
    M->col_head = (linklist *) malloc((n + 1) * sizeof(linklist));
    for (k = 1; k <= n; k++) {
        M->col_head[k] = NULL;
    }
    printf("输入非零元素行，列，非零元素\n");
    for (k = 0; k < t; k++) {
        scanf("%d%d%d", &i, &j, &e);
//      判断 是否重复的输入数据，如果重复则跳过
        for (judge_number = 1; judge_number <= m; judge_number++) {
            judge = M->row_head[judge_number];
            while (judge != NULL) {
                if (judge->i == i && judge->j == j) {

                    break;
                }
                judge = judge->right;
            }
        }
//      判断是不是超出范围
        if (i > M->mu || j > M->nu) {
            printf("位置不合法!  无法完成操作!\n");
            system("pause");
            exit(0);
        }
//      新建立的结点进行初始化
        bulid = (linklist) malloc(sizeof(node));
        bulid->i = i;
        bulid->j = j;
        bulid->e = e;
        bulid->right = NULL;
        bulid->down = NULL;
//      完成行插入
        if (M->row_head[i] == NULL || M->row_head[i]->j > j) {
            bulid->right = M->row_head[i];
            M->row_head[i] = bulid;
        } else {
            p = M->row_head[i];
            while (p->right != NULL && p->right->j < j) {
                p = p->right;
            }
            bulid->right = p->right;
            p->right = bulid;
        }
//      完成列插入
        if (M->col_head[j] == NULL || M->col_head[j]->i > i) {
            bulid->down = M->col_head[j];
            M->col_head[j] = bulid;
        } else {
            p = M->col_head[j];
            while (p->down != NULL && p->down->i < i) {
                p = p->down;
            }
            bulid->down = p->down;
            p->down = bulid;
        }
    }
    return ok;
}

void print_list(cross_list *M) {
    int row_i, col_j;
    linklist print;
    printf("稀疏矩阵为\n");
    for (row_i = 1; row_i <= M->mu; row_i++) {
        print = M->row_head[row_i];
        for (col_j = 1; col_j <= M->nu; col_j++) {
            if (print != NULL && print->j == col_j) {
                printf("%d\t", print->e);
                print = print->right;
            } else {
                printf("%d\t", NULL);
            }
        }
        printf("\n");
    }
}

int main() {
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
    cross_list *M = (cross_list*)malloc(sizeof(cross_list));
    initCrossList(M);
    createCrossList(M);
    print_list(M);
    return 0;
}
 