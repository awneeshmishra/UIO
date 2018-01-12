#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/io.h>
#include <linux/interrupt.h>
#include <linux/fs.h>
#include <linux/string.h>
#include <linux/uaccess.h>
#include <linux/device.h>
#include <linux/cdev.h>
#include <linux/of_address.h>
#include <linux/of_device.h>
#include <linux/of_platform.h>
#include <linux/errno.h>
#include <asm/io.h>
#include <linux/sched.h>
#include <linux/uio_driver.h>

MODULE_AUTHOR("Awneesh") ;
MODULE_DESCRIPTION("UIO Driver for svd") ; 
MODULE_LICENSE("GPL");

#define DRIVER_NAME "svd-uio"

static struct uio_info *info ; 
static struct device *dev ; 

static struct resource *r_mem ;
static int irq ; 

static irqreturn_t my_handler(int irq, struct uio_info *dev_info)
{
   static int count = 0 ; 
   pr_info("In UIO handler, count = %d\n", count++) ; 
   /*  Must return IRQ_HANDLED for event to reach uspace  */
   return IRQ_HANDLED ; 
}


static int uio_probe(struct platform_device *pdev)
{
  struct resource *r_irq ; 
  //dev = kzalloc(sizeof(struct device), GFP_KERNEL) ; 
  //dev = &pdev->dev ; 
   
  irq = platform_get_irq(pdev, 0) ;

  //struct device *dev = &pdev->dev ; 
  
  //dev_info(dev, "DeviceTree Probing");
  /*  Get iospace for the device */

  r_mem = platform_get_resource(pdev, IORESOURCE_MEM, 0);
  if (!r_mem) {
             return -ENODEV ; 
      }

  if (!request_mem_region ( r_mem->start, r_mem->end - r_mem->start + 1, "svd_uio")) {
           printk("Couldn't lock memory region at %p\n", (void *)r_mem->start);
           
            return -EBUSY ;  
      }

  info = kzalloc(sizeof(struct uio_info), GFP_KERNEL) ; 
  info->name = "uio-device" ; 
  info->version = 1 ; 
  info->irq = irq ; 
  info->irq_flags = IRQF_SHARED ; 
  info->handler = my_handler ; 
  info->mem[0].name = "registers" ; 
  info->mem[0].addr = r_mem->start ; 
  info->mem[0].size = resource_size(r_mem) ; 
  info->mem[0].memtype = UIO_MEM_PHYS ; 
    
  //device_register(dev) ;  

  if (uio_register_device(&pdev->dev, info) < 0) {
    // kfree(dev) ; 
     kfree(info) ; 
     pr_info("Failing to register uio device\n") ; 
     return -1 ; 
  }
  pr_info("Registered UIO handler for IRQ = %d\n",irq) ; 
  return 0;
}

static int uio_remove(struct platform_device *pdev)
{
 uio_unregister_device(info) ;  
 free_irq(irq, &pdev->dev) ; 
 release_mem_region(r_mem->start, r_mem->end - r_mem->start + 1 ) ; 
 kfree(info) ; 
 //kfree(dev) ; 
 return 0  ;
}

static struct of_device_id svd_of_match[] = {
               { .compatible = "xlnx,svd-1.0"} , 
               {} , 
   } ; 

MODULE_DEVICE_TABLE(of,svd_of_match) ;

static struct platform_driver  svd_driver  = {
                   .driver = {
                             .name = DRIVER_NAME ,
                             .owner = THIS_MODULE, 
                             .of_match_table = svd_of_match , 
                      },
                   .probe =  uio_probe  ,
                   .remove = uio_remove ,
} ; 
                  

static int __init uio_init(void)
{
  printk ("<1>Hello Module World  - Frpm Driver\n") ;
  return platform_driver_register(&svd_driver) ; 

}

static void __exit uio_exit(void)
{
  platform_driver_unregister(&svd_driver) ; 
}

module_init(uio_init) ; 
module_exit(uio_exit) ; 

