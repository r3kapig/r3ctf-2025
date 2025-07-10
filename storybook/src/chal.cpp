#include <cstddef>
#include <cstdlib>
#include <iterator>
#include<print>
#include<string>
#include<cstring>
#include<iostream>
#include<cstdio>
#include<algorithm>
#include<stdexcept>

template<typename T, std::size_t N>
struct inplace_vector {
    inplace_vector() = default;
    ~inplace_vector() {
        std::for_each_n(reinterpret_cast<T*>(data_), size_, [](T& obj){obj.~T();});
    }
    inplace_vector(const inplace_vector<T, N>& other) {
        std::copy_n(static_cast<const T*>(data_), other.size_, static_cast<T*>(other.data_));
        size_ = other.size_;
    }
    inplace_vector(inplace_vector<T,N>&& other) {
        std::copy_n(std::make_move_iterator(static_cast<T*>(other.data_)), other.size_, static_cast<T*>(data_));
        size_ = other.size_;
        other.size_ = 0;
    }

    T* data() {
        return reinterpret_cast<T*>(data_);
    }
    
    const T* data() const {
        return reinterpret_cast<const T*>(data_);
    }

    template<typename... Args>
    void emplace_back(Args... args){
        if (size_ == N) {
            throw std::out_of_range("out of range");
        }
        new (data() + size_++) T(args...);
    }

    T& operator[](std::size_t idx) {
        return data()[idx];
    }
    
    const T& operator[](std::size_t idx) const {
        return data()[idx];
    }

    T& at(std::size_t idx) {
        if (idx >= size_)
            throw std::out_of_range("index out of bounds");
        return data()[idx];
    }

    const T& at(std::size_t idx) const {
        if (idx >= size_)
            throw std::out_of_range("index out of bounds");
        return data()[idx];
    }

    std::size_t size() const {
        return size_;
    }

private:
    std::size_t size_ = 0;
    alignas(T) std::byte data_[N * sizeof(T)];
};

struct story {
    story() {
        buf[0] = '\0';
    }

    story(const char* s){
        if(std::strlen(s) >= sizeof(this->buf)){
            throw std::out_of_range("Your story is tooooooo long");
        }
        std::strcpy(this->buf, s);
    }

    story(const std::string& s){
        if(std::strlen(s.data()) >= sizeof(this->buf)){
            throw std::out_of_range("Your story is tooooooo long");
        }
        if(s.empty())
            buf[0] = '\0';
        std::memcpy(buf, s.data(), s.size());
    }
    
    char* data() {
        return buf;
    }
    
    const char* data() const {
        return buf;
    }

private:
    char buf[128];
};

auto menu = []{
    std::println("1. Create a story");
    std::println("2. Write down a story");
    std::println("3. Read out a story");
    std::print(">> ");
};

inline void expect(bool c) {
    if (!c)
        std::abort();
}

int main(){
    std::setbuf(stdin, nullptr);
    std::setbuf(stdout, nullptr);
    std::setbuf(stderr, nullptr);
    
    std::println("When I was very young, I love reading story books");
    std::string input_buf{};
    inplace_vector<story, 8> stories;

    while(true){
        menu();
        unsigned choice;
        unsigned idx;
        expect(std::scanf("%u", &choice) == 1);
        switch (choice) {
            case 1:
                std::println("Please input your story");
                std::cin>>input_buf;
                break;
            case 2:
                std::println("Sure!");
                stories.emplace_back(input_buf);
                break;
            case 3:
                std::println("Please input index");
                expect(std::scanf("%u", &idx) == 1);
                std::print("{}", stories.at(idx).data());
                break;
            default:
                return 0;
        }
    }
}
