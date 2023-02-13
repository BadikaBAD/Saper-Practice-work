#include <stdlib.h>
#include <stdlib.h>
#include <assert.h>

#include "mines.h"

#define NEIGHBORS_MAP_H 8
#define NEIGHBORS_MAP_W 2
const int neighbors_map[NEIGHBORS_MAP_H][NEIGHBORS_MAP_W] = {
        {-1, 1},
        {0,  1},
        {1,  1},
        {1,  0},
        {1,  -1},
        {0,  -1},
        {-1, -1},
        {-1, 0}
};


static Cell** new_cells(Minefield* self,
    int width,
    int height);

static void init_mines(Minefield* self,
    int mines);

static void count_mines_around(Minefield* self);

static bool is_allowed_cell(Minefield* self,
    int x,
    int y);

static void open_recursive(Minefield* self,
    int x,
    int y);


void
init_minefield(
    Minefield* self,
    int width,
    int height,
    int mines_n)
{

    self->_width = width;
    self->_height = height;
    self->_mines_n = mines_n;

    self->_cells = new_cells(self, width, height);
    init_mines(self, mines_n);
    count_mines_around(self);

}

void
free_minefield(Minefield* self)
{
    for (int y = 0; y < self->_height; y++) {
        free(self->_cells[y]);
    }
    free(self->_cells);
}

void
open(Minefield* self,
    int x,
    int y)
{
    if (!is_allowed_cell(self, x, y)) {
        return;
    }

    Cell* cell = &(self->_cells[y][x]);

    if (cell->_flagged) {
        return;
    }

    if (cell->_mined) {
        self->_exploded = true;
        cell->_opened = true;
        return;
    }

    open_recursive(self, x, y);
}

void
flag(Minefield* self,
    int x,
    int y)
{
    if (!is_allowed_cell(self, x, y)) {
        return;
    }

    Cell* cell = &(self->_cells[y][x]);

    if (cell->_opened) {
        return;
    }

    cell->_flagged = !cell->_flagged;
}

bool
is_win(Minefield* self)
{
	int good_flags = 0;
	for (int y = 0; y < self->_height; y++) {
		for (int x = 0; x < self->_width; x++) {
			Cell *cell = &(self->_cells[y][x]);

			if (cell->_flagged && cell->_mined) {
				good_flags++;
			}
		}
	}

	return (self->_opened_n + good_flags) == (self->_width * self->_height - self->_mines_n);
}

static Cell**
new_cells(Minefield* self,
    int width,
    int height)
{

    Cell** cells = malloc(sizeof(Cell*) * self->_height);
    assert(cells != NULL || "ALLOCATION FAILED");

    for (int y = 0; y < self->_height; y++) {
        cells[y] = malloc(sizeof(Cell) * self->_width);
        assert(cells[y] != NULL || "ALLOCATION FAILED");

        for (int x = 0; x < self->_width; x++) {
            cells[y][x] = (Cell){
                    ._mined = false,
                    ._opened = false,
                    ._flagged = false,
                    ._mines_around = 0,
            };
        }
    }

    return cells;
}

static void
init_mines(Minefield* self,
    int mines)
{
    while (mines > 0) {
        int x = rand() % self->_width;
        int y = rand() % self->_height;

        Cell *cell = &(self->_cells[y][x]);

        if (!cell->_mined) {
            cell->_mined = true;
            mines--;
        }
    }
}

static bool
is_allowed_cell(Minefield* self,
    int x,
    int y)
{
    return x >= 0 && x < self->_width&& y >= 0 && y < self->_height;
}

static void
count_mines_around(Minefield* self)
{
    for (int y = 0; y < self->_height; y++) {
        for (int x = 0; x < self->_width; x++) {
            for (int i = 0; i < NEIGHBORS_MAP_H; i++) {

                int neighbor_x = x + neighbors_map[i][0];
                int neighbor_y = y + neighbors_map[i][1];

                if (is_allowed_cell(self, neighbor_x, neighbor_y)
                    && self->_cells[neighbor_y][neighbor_x]._mined) {

                    self->_cells[y][x]._mines_around++;
                }
            }
        }
    }
}

static void open_recursive(Minefield* self,
    int x,
    int y)
{
    Cell* cell = &(self->_cells[y][x]);

    if (cell->_opened) {
        return;
    }

    self->_opened_n += (cell->_opened = true);

    if (!cell->_mined && cell->_mines_around == 0) {
        for (int i = 0; i < NEIGHBORS_MAP_H; i++) {

            int neighbor_x = x + neighbors_map[i][0];
            int neighbor_y = y + neighbors_map[i][1];

            if (is_allowed_cell(self, neighbor_x, neighbor_y)) {
                open_recursive(self, neighbor_x, neighbor_y);
            }
        }
    }
}
