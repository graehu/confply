#include <chrono>
#include <iomanip>
#include <iostream>
#include <memory>

std::chrono::high_resolution_clock my_clock;

int main()
{
   std::cout << "hello confply!" << std::endl;
   auto now = my_clock.now();
   int my_var = 1000;
   for (int i = 0; i < 100000000; i++)
   {
      my_var += i * i;
   }
   std::cout << "time wasting calculation result: " << my_var << std::endl;
   std::chrono::duration<double, std::micro> microsecs = my_clock.now() - now;
   std::chrono::duration<double, std::milli> millisecs = my_clock.now() - now;
   std::cout << "time wasted: " << microsecs.count() << "u"
	     << "(" << millisecs.count() << "ms)" << std::endl;

   return 0;
}
