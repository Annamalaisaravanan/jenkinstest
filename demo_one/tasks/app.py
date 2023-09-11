from demo_one.common import Task



class DataPrep(Task):

    def hello_world(self):
                print("Hello World")
                print("The sum is {}".format(self.conf['sum']['a'] + self.conf['sum']['b']))
                

                   
    
    def launch(self):
         
         self.hello_world()

   

def entrypoint():  
    
    task = DataPrep()
    task.launch()


if __name__ == '__main__':
    entrypoint()