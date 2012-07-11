#****************************************************************************#
# mutation-call-by-coverage
#$Id: cheapseq.mak 1772 2012-07-10 08:01:52Z favorov $
#****************************************************************************#
name=noiser
exename=$(name)

td=.
od=./obj

srcdirlist=$(td)

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


OBJS=$(od)/$(name).o


objs:$(OBJS)

$(od)/%.o: %.c
	$(CC) $(CCFLAGS) $< -o $@
	
$(od)/%.o: %.cpp
	$(CPP) $(CPPFLAGS) $< -o $@

$(exename)$(EXEEXT): $(OBJS)
	$(CPP) -o $(exename)$(EXEEXT) $(OBJS) $(LINKFLAGS)
	chmod 755 $(exename)$(EXEEXT) 

$(od)/$(name).o: $(name).cpp

clean:
	rm -f $(OBJS)
	rm -r -f *~

fullclean: clean
	rm -f $(exename)$(EXEEXT)
	
