#include <iostream>
#include <string>
#include <Windows.h>

using namespace std;

int main()
{ 
    cout << "Carregando app SRO Correios v1.8" << endl;
    cout << "Aguarde o processamento dos dados." << endl;
    string filename = "correios_reading.py";
    string command = "python ";
    command += filename;
    system(command.c_str());
}