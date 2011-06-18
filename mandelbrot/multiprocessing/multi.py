import itertools
import multiprocessing
import sys
import datetime
# area of space to investigate
x1, x2, y1, y2 = -2.13, 0.77, -1.3, 1.3

# as for pure_python_2.py with z[i], q[i] dereferences removed


def calculate_z_serial_purepython(inps):
    q, maxiter, z = inps
    output = [0] * len(q)
    for i in range(len(q)):
        zi = z[i]
        qi = q[i]
        if i % 1000 == 0:
            # print out some progress info since it is so slow...
            print "%0.2f%% complete" % (1.0/len(q) * i * 100)
        for iteration in range(maxiter):
            zi = zi * zi + qi
            if abs(zi) > 2.0:
                output[i] = iteration
                break
    return output


def flatten(listOfLists):
    "Flatten one level of nesting, recipe from itertools"
    items_it = itertools.chain.from_iterable(listOfLists)
    return [item for item in items_it]


def calc_pure_python(show_output):
    # make a list of x and y values which will represent q
    # xx and yy are the co-ordinates, for the default configuration they'll look like:
    # if we have a 1000x1000 plot
    # xx = [-2.13, -2.1242, -2.1184000000000003, ..., 0.7526000000000064, 0.7584000000000064, 0.7642000000000064]
    # yy = [1.3, 1.2948, 1.2895999999999999, ..., -1.2844000000000058, -1.2896000000000059, -1.294800000000006]
    x_step = (float(x2 - x1) / float(w)) * 2
    y_step = (float(y1 - y2) / float(h)) * 2
    x=[]
    y=[]
    ycoord = y2
    while ycoord > y1:
        y.append(ycoord)
        ycoord += y_step
    xcoord = x1
    while xcoord < x2:
        x.append(xcoord)
        xcoord += x_step
    q = []
    for ycoord in y:
        for xcoord in x:
            q.append(complex(xcoord,ycoord))
    z = [0+0j] * len(q)

    print "Total elements:", len(z)


    # split work list into continguous chunks, one per CPU
    # build this into chunks which we'll apply to map_async
    chunk_size = len(q) / multiprocessing.cpu_count()
    #chunk_size = len(q) / 4 # 4 not really faster than 2
    chunks = []
    chunk_number = 0
    while True:
        # create a chunk of chunk_size for (q, maxiter, z)
        chunk = (q[chunk_number * chunk_size:chunk_size*(chunk_number+1)], maxiter, z[chunk_number * chunk_size:chunk_size*(chunk_number+1)]) 
        chunks.append(chunk)
        chunk_number += 1
        if chunk_size * chunk_number > len(q):
            break
    #print chunk_size, len(chunks), len(chunks[0][0])

    # create a Pool which will create Python processes
    p = multiprocessing.Pool()
    start_time = datetime.datetime.now()
    # send out the work chunks to the Pool
    # po is a multiprocessing.pool.MapResult
    po = p.map_async(calculate_z_serial_purepython, chunks)
    # we get a list of lists back, one per chunk, so we have to
    # flatten them back together
    # po.get() will block until results are ready
    results = po.get() # [[ints...], [ints...], []]
    output = flatten(results) # flatten the results and ignore empty list
    end_time = datetime.datetime.now()

    secs = end_time - start_time
    print "Main took", secs

    validation_sum = sum(output)
    print "Total sum of elements (for validation):", validation_sum

    if show_output: 
        import Image
        import numpy as nm
        output = nm.array(output)
        output = (output + (256*output) + (256**2)*output) * 8
        im = Image.new("RGB", (w/2, h/2))
        # you can experiment with these x and y ranges
        im.fromstring(output.tostring(), "raw", "RGBX", 0, -1)
        im.show()

if __name__ == "__main__":
    # get width, height and max iterations from cmd line
    # 'python mandelbrot_pypy.py 100 300'
    w = int(sys.argv[1]) # e.g. 100
    h = int(sys.argv[1]) # e.g. 100
    maxiter = int(sys.argv[2]) # e.g. 300
    
    # we can show_output for Python, not for PyPy
    calc_pure_python(True)
