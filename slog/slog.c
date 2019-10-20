//
// Created by chaos wang on 2019-09-18.
//

#include "slog.h"
#include <stdio.h>
#include <stdarg.h>

int slog_log(const int priority, const char* fmt, ...)
{
    va_list ap;
    char *buf = NULL;
    int buflen = 0;
    va_start(ap, fmt);
    vsnprintf(buf, buflen, fmt, ap);

    vfprintf()
}

int main(void)
{
    printf("hello world\n");
    return 0;
}
