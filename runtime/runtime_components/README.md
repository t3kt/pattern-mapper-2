# Runtime Components

This directory contains components used in the runtime system which are reusable. Typically these are things that are
cloned elsewhere in the system. Things that are effectively singletons (like the state management subsystem) should not
go in this folder, though they may contain clones of these components. 
