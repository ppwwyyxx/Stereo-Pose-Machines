PYLON_PATH ?= /opt/pylon5

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	CXX ?= g++
endif
INCLUDE_DIR = -I. -isystem $(PYLON_PATH)/include -isystem third_party
INCLUDE_DIR += $(shell python-config --cflags | cut -d ' ' -f 1)

ifneq (,$(findstring clang,$(CXX)))
	OMP_FLAG=-fopenmp=libomp
else
	OMP_FLAG=-fopenmp
endif

OPTFLAGS ?= -O3 -msse3 -march=native
#OPTFLAGS ?= -g3 -fsanitize=address,undefined -O0
DEFINES = -DDEBUG  	# comment out this line improves speed

# optional extra packages
LIBS = opencv
INCLUDE_DIR += $(shell pkg-config --cflags $(LIBS))
LDFLAGS += $(shell pkg-config $(LIBS) --libs)
LDFLAGS += $(shell $(PYLON_PATH)/bin/pylon-config --libs)
LDFLAGS += $(shell $(PYLON_PATH)/bin/pylon-config --libs-rpath)
LDFLAGS += $(shell python-config --libs)

CXXFLAGS += -fPIC
CXXFLAGS += $(INCLUDE_DIR) $(OMP_FLAG) -Wall -Wextra
CXXFLAGS += $(DEFINES) -std=c++11 $(OPTFLAGS)
CXXFLAGS += -DUSE_GIGE

LDFLAGS += $(OPTFLAGS)
LDFLAGS += $(OMP_FLAG)

SHELL = bash
OBJ_DIR = obj
ccSRCS = $(shell find . -name "*.cc" | sed 's/^\.\///g')
MAIN_SRCS := $(shell find -L -name "*.cpp" | cut -c 3- | grep -v '^_')

OBJS = $(addprefix $(OBJ_DIR)/,$(ccSRCS:.cc=.o))
MAIN_OBJ  := $(addprefix $(OBJ_DIR)/, $(MAIN_SRCS:.cpp=.o))
DEPS = $(OBJS:.o=.d) $(MAIN_OBJ:.o=.d)
BINS = $(MAIN_SRCS:.cpp=.bin)
SO = libcpm.so

.PHONY: all clean run

all: $(BINS) $(SO)

ifneq ($(MAKECMDGOALS), clean)
sinclude $(DEPS)
endif

$(SO): $(OBJS)
	@echo "[$(SO)] ..."
	@$(CXX) $(CXXFLAGS) $(LDFLAGS) $^ -fPIC -shared -o $@


$(BINS): %.bin: $(OBJS) %.cpp
	@echo "[bin] $@ ..."
	@$(CXX) $^ -o $@ $(CXXFLAGS) $(LDFLAGS)

$(OBJ_DIR)/%.o: %.cc
	@echo "[cc] $< ..."
	@$(CXX) -c $< -o $@ $(CXXFLAGS)

$(OBJ_DIR)/%.d: %.cc Makefile
	@mkdir -p $(dir $@)
	@echo "[dep] $< ..."
	@$(CXX) $(CXXFLAGS) $(DEFINES) -MM -MT "$(OBJ_DIR)/$(<:.cc=.o) $(OBJ_DIR)/$(<:.cc=.d)" "$<"  > "$@"

clean:
	@rm -rvf $(OBJ_DIR) $(BINS)

