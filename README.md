# Total, a tribute to awk

While writing my last post I made up some syntax ( pseudo syntax ) that dose not work, for a command that dose not exist... however I think that it should.

The syntax was to get the average CPU idle time from the last 3 seconds, via the vmstat command.

```sh
vmstat 1 3 | total '$id:average'
```

This made me stop writing the post and start working on the new command and then this post.

[![Build Status](https://travis-ci.org/daniellawrence/total.png?branch=master)](https://travis-ci.org/daniellawrence/total)

total
------

The command is called *total* and is very much inspired by awk.

The total command is a trade in awk massive power inlue of easy syntax, for the common problems.


example time
-------------

The problem that I was facing working out the average of a set of numbers generated by a command: in this case it was *vmstat*

```sh
$ vmstat 1 3
procs -----------memory---------- ---swap-- -----io---- -system-- ----cpu----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa
 0  0      0 6207264  85564 949404    0    0    29     4  107  178  2  1 98  0
 0  0      0 6201800  85564 955036    0    0     0     0  403  396  0  0 100  0
 0  0      0 6201552  85572 955244    0    0     0    80  591  677  2  1 98  0
```

I wanted to grab the average cpu idle, this is case it is column 15, pictured above its values are: 'id', '98', '100' and '98'

```sh
$ vmstat 1 3 | awk 'BEGIN {id_total=0; count=0}
{id_total+=$15;count+=1}
END{print id_total/count}'
```

The above is a try at doing this in awk, however i know that is going to fail because one of the values is 'id', which is not a number.

Enter total
-----------

To add everything up in the 15th column, you just need the syntax of '''$15'''

```sh
$ vmstat 1 3 | total '$15'
297
```

One of the advantages of total is that its *header aware*.
In the case of the first sample of vmstat, it will understand that the 15 column is called "id".

This means that you can do the following, to get the total id.

```sh
$ vmstat 1 3 | total '$id'
297
```

You can reference the data as either the name of the column (:total is the default)
```sh
# vmstat 1 3 | ./total/total.py '$cache $cache:total $6 $6:total'
8262988 8262988 8262988 8262988
```

Totaling or a Sum is nice, However the total amount of idle cpu time isn't a very good marker.
What you really want is the average id...

```sh
$ vmstat 1 3 | total '$id:avg'
99
```

Or maybe just the max id

```sh
$ vmstat 1 3 | total '$id:max'
100
```

Or maybe you want to have this formatted for a email or alert.

```sh
$ vmstat 1 3 | total 'The average idle cpu was $id:avg, with the max of $id:max'
The average idle cpu was 97, with the max of 98
```


OR maybe something crazy like the average cache minus the average buff

```sh
vmstat 1 2 | total '$cache:avg - $buff:avg'|bc
1932560
```

To get a list of all the *keys* that can be used in the *$* ( dollar ) notation you can just run total with --list

```sh
$ vmstat 1 2 | totat --list ''
You can use the following cols for: :total, :avg, :min, :max
bo, buff, cache, cs, free, id, in, r, si, so, swpd, sy, us, wa
```

Its not just for vmstat either...

```sh
netstat -i | total --list ''
You can use the following cols for: :total, :avg, :min, :max
flg, iface, met, mtu, rx-drp, rx-err, rx-ok, rx-ovr, tx-drp, tx-err, tx-ok, tx-ovr
```

How to Install!
--------

Quick hack install
```sh
$ curl https://raw.github.com/daniellawrence/total/master/total/total.py > total
$ chmod a+x total
```

Install from pip

```sh
$ sudo pip install total
# test
$ vmstat 1 3 | total '$id:avg'
```

Install from source

```sh
$ git clone git://github.com/daniellawrence/total
$ cd total
$ sudo ./setup.py install
# test
$ vmstat 1 3 | total '$id:avg'
```
