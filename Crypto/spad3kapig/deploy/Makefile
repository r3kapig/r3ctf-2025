BUILD_DIR ?= ./build
SRC_DIR ?= ./src
PRIV_DIR ?= ./priv

TARGET ?= Spad3kapig

CC := clang
CXX := clang++

CPPFLAGS ?= -MD
CFLAGS ?= -g -Wall -Werror
CXXFLAGS ?= -g -Wall -Werror -std=c++20 -O3
LDFLAGS ?= -g -std=c++20

SRCS := $(shell find $(SRC_DIR) -name "*.cpp")
OBJS := $(SRCS:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
DEPS := $(OBJS:.o=.d)

UNAME_S := $(shell uname -s)

$(BUILD_DIR)/$(TARGET): $(BUILD_DIR)/$(TARGET)-unstripped
ifeq ($(UNAME_S),Darwin)
	strip -x $< -o $@
else
	strip --strip-unneeded $< -o $@
endif


$(BUILD_DIR)/$(TARGET)-unstripped: $(OBJS)
	$(CXX) $(filter-out ./build/XXXXX.o,$(OBJS)) -o $@ $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	mkdir -p $(dir $@)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

.PHONY: clean run all

all: $(BUILD_DIR)/$(TARGET)

run: $(BUILD_DIR)/$(TARGET)
	$<

clean:
	rm -rf $(BUILD_DIR)

-include $(DEPS)