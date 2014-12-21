
# .Wall

## .touchback(future)
This removes the future instance from the list of futures
that are waiting. When this list has zero elements left,
the .running Event gets set. The value of .result() is
appended to the .received list.

## .prepare(future)
Adds the future instance to the waiting queue.

## .wait
This returns all received results after waiting for all of them
to be retreived ( when .running.wait() returns, in other words ).
If there are no results waiting to be retreived, the results are
simply returned and no call to .running.wait is made.
