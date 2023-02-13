#ifndef MINES_H
#define MINES_H

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#elif linux
#define EXPORT
#endif

#include <stdbool.h>


typedef struct Cell {
    bool _mined;
    bool _opened;
    bool _flagged;
    int _mines_around;
} Cell;


typedef struct Minefield {
    int _width;
    int _height;
    Cell **_cells;

    int _mines_n;
    int _opened_n;
    int _flagged_n;

    bool _exploded;
} Minefield;

EXPORT void init_minefield(Minefield *self,
                           int width,
                           int height,
                           int mines_n);

EXPORT void free_minefield(Minefield *self);

EXPORT void open(Minefield *self,
                 int x,
                 int y);

EXPORT void flag(Minefield *self,
                 int x,
                 int y);

EXPORT bool is_win(Minefield *self);

#endif
