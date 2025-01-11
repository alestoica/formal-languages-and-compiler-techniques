bits 32
global start
extern exit
import exit msvcrt.dll
extern printf
import printf msvcrt.dll
extern scanf
import scanf msvcrt.dll


segment data use32 class=data

write_int_fmt DB "%d ", 0
write_line_fmt DB 0xA, 0x0
read_int_fmt DB "%i", 0

 sum DD 0
 b DD 0
 a DD 0
 temp1 DD 0
 temp2 DD 0


segment code use32 class=code


start:
 
 mov EAX, a
 push EAX
 push dword read_int_fmt
 call [scanf]
 add ESP, 8
 
 mov EAX, b
 push EAX
 push dword read_int_fmt
 call [scanf]
 add ESP, 8
 
 mov eax, [b]
 imul eax, 3
 mov [temp1], eax

 
 mov eax, [a]
 add eax, [temp1]
 mov [temp2], eax

 
 
 
 
 


 
 mov eax, [temp2]

 
 mov [sum], eax

 
 mov EAX, [sum]
 push EAX
 push dword write_int_fmt
 call [printf]
 add ESP, 8

 
 push dword write_line_fmt
 call [printf]
 add ESP, 4

 push dword 0
 call [exit]
