#****************************************************************************#
# mutation-call-by-coverage
#$Id$
#****************************************************************************#
name=cheapseq
exename=$(name)

td=.
dd=./dna
cd=./control
od=./obj

srcdirlist=$(dd):$(cd):$(td)

empty=
space=$(empty) $(empty)
includeflags = $(foreach dir,$(subst :,$(space),$(srcdirlist)),$(INCLUDEKEY)$(dir)) $(INCLUDECLOSETERM)
#this strange invocation is just preparing -I flag from srcdirlist.

include ~/include/ccvars
include ~/include/boostdirs

CPPFLAGS:=$(CPPFLAGS) -I $(boost_include)
LINKFLAGS:=$(LINKFLAGS) -L $(boost_lib) -lboost_iostreams -lboost_program_options

.PHONY: all objs clean fullclean

vpath %.c $(srcdirlist)
vpath %.cpp $(srcdirlist)
vpath %.h $(srcdirlist)
vpath %.hpp $(srcdirlist)


all: $(exename)$(EXEEXT) 


OBJS=$(od)/$(name).o \
$(od)/Sequences.o 


objs:$(OBJS)

$(od)/%.o: %.c
	$(CC) $(CCFLAGS) $< -o $@
	
$(od)/%.o: %.cpp
	$(CPP) $(CPPFLAGS) $< -o $@

$(exename)$(EXEEXT): $(OBJS)
	$(CPP) -o $(exename)$(EXEEXT) $(OBJS) $(LINKFLAGS)
	chmod 755 $(exename)$(EXEEXT) 

$(od)/$(name).o: $(name).cpp mutation.hpp Exception.hpp Sequences.hpp Atgc.hpp $(name)_config.hpp
$(od)/Sequences.o: Sequences.cpp Sequences.hpp Exception.hpp Atgc.hpp 

clean:
	rm -f $(OBJS)
	rm -r -f *~

fullclean: clean
	rm -f $(exename)$(EXEEXT)
	
