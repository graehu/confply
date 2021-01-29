#include <chrono>
#include <iomanip>
#include <iostream>
#include <memory>

static std::chrono::high_resolution_clock my_clock;
static int fib(int n) 
{ 
    if (n <= 1) 
        return n;
    return fib(n-1) + fib(n-2); 
} 

int main()
{
   std::cout << "hello confply!" << std::endl;
   auto now = my_clock.now();
   int my_var = fib(40);

   std::cout << "time wasting calculation result: " << my_var << std::endl;
   std::chrono::duration<double, std::micro> microsecs = my_clock.now() - now;
   std::chrono::duration<double, std::milli> millisecs = my_clock.now() - now;
   std::cout << "time wasted: " << microsecs.count() << "u"
	     << "(" << millisecs.count() << "ms)" << std::endl;

   return 0;
}
