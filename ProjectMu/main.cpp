#include <iostream>
#include <ctime>

int biomes = 20;


int main() {
    int arr[1000][500];    
    srand(100/*static_cast<unsigned int>(time(nullptr))*/);
    int randomNumber = rand();
    std::cout << "Random number: " << randomNumber << std::endl;
    std::cout << "Hello, world!" << std::endl;
    return 0;
}