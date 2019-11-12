//
// Created by chaos wang on 2019/11/12.
//

#ifndef ORTHOGONAL_LIST_ORTHOGONALLIST_H
#define ORTHOGONAL_LIST_ORTHOGONALLIST_H

typedef struct Orthogonal_linked_list_node
{
    float some_data;
    int row;
    int column;
    struct _matrix_element *next_row;
    struct _matrix_element *next_column;
}matrixNode;

#endif //ORTHOGONAL_LIST_ORTHOGONALLIST_H
