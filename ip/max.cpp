
//Maximum Array Size
#define MAX_SIZE 16

//TRIPCOUNT identifier
typedef float DTYPE;

// one-dimensional version
extern "C" {
void argmax(const int *a, // Read-Only array A
           int* max,       // Output Result
           int size    // array A Size
) {
   #pragma HLS INTERFACE m_axi port=a offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=minindex offset=slave bundle=gmem

   #pragma HLS INTERFACE s_axilite port=a bundle=control
   #pragma HLS INTERFACE s_axilite port=minindex bundle=control
   #pragma HLS INTERFACE s_axilite port=size bundle=control
   #pragma HLS INTERFACE s_axilite port=return bundle=control

    *max = a[0];
    int maxindex = 0;
    
    for (int i=0; i<size; i++){
        if (a[i]> *max){
            *max = a[i] ; 
            maxindex = i ; 
        }
    }
}
}